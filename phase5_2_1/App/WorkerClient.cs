using System.Diagnostics;
using System.Text.Json;
namespace PdfPrototype;
public sealed class WorkerClient:IDisposable
{
 internal Func<EditRequest,Task>? BeforeDeliveryForControlTest;
 long calls;
 public long Calls=>Interlocked.Read(ref calls);
 Process? process; readonly SemaphoreSlim gate=new(1,1);
 void Start()
 {
  if(process!=null&&!process.HasExited)return;
  var start=new ProcessStartInfo(Path.Combine(AppContext.BaseDirectory,"PdfWorker.exe")){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,CreateNoWindow=true,WindowStyle=ProcessWindowStyle.Hidden,WorkingDirectory=AppContext.BaseDirectory,StandardInputEncoding=new System.Text.UTF8Encoding(false),StandardOutputEncoding=System.Text.Encoding.UTF8};
  process=Process.Start(start)??throw new IOException("Cannot start PDF worker.");process.ErrorDataReceived+=(s,e)=>{};process.BeginErrorReadLine();
 }
 public async Task<T> Call<T>(EditRequest request)
 {
  Interlocked.Increment(ref calls);
  await gate.WaitAsync();
  try
  {
   Start();await process!.StandardInput.WriteLineAsync(Wire.Write(request));await process.StandardInput.FlushAsync();
   string? line=await process.StandardOutput.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(30));
   if(line==null)throw new IOException("PDF worker ended. Draft retained; the next request will restart it.");
   var result=Wire.Read<Envelope>(line);
   if(result.Revision!=request.Revision)throw new IOException("Worker revision mismatch; draft retained.");
   if(!result.Ok)throw new IOException(result.Error);
   if(BeforeDeliveryForControlTest!=null)await BeforeDeliveryForControlTest(request);
   return result.Data!.Value.Deserialize<T>(Wire.Options)!;
  }
  catch(Exception e)when(e is TimeoutException||e is EndOfStreamException)
  {if(process!=null&&!process.HasExited)process.Kill(true);throw new IOException("Worker timed out. Draft retained; retry will restart processing.",e);}
  finally{gate.Release();}
 }
 public void Dispose(){if(process!=null&&!process.HasExited){process.StandardInput.Close();if(!process.WaitForExit(500))process.Kill(true);}process?.Dispose();}
 internal void TerminateForControlTest(){if(process!=null&&!process.HasExited){process.Kill(true);process.WaitForExit();}}
}
