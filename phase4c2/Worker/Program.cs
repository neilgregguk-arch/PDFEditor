using PdfPrototype;
using System.IO;
using System.Text.Json;
Console.InputEncoding=System.Text.Encoding.UTF8;Console.OutputEncoding=new System.Text.UTF8Encoding(false);
var engine=new PdfEngine();
if(args.Length>0&&args[0]=="--samples"){PdfEngine.GenerateSamples(Path.GetFullPath(args[1]));return;}
string? line;
while((line=Console.ReadLine())!=null)
{
 long revision=0;
 try
 {
  var request=Wire.Read<EditRequest>(line);revision=request.Revision;
  object result=request.Command=="inspect"?engine.Inspect(request):engine.Edit(request);
  Console.WriteLine(Wire.Write(new{Revision=revision,Ok=true,Data=result,Error=(string?)null}));
 }
 catch(Exception e){Console.WriteLine(Wire.Write(new{Revision=revision,Ok=false,Data=(object?)null,Error=e.Message}));}
}
