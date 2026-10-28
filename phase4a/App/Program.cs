using System.Windows;
namespace PdfPrototype;
public static class Program
{
 [STAThread] public static void Main(string[] args)
 {
  var app=new Application();app.DispatcherUnhandledException+=(s,e)=>{MessageBox.Show("Prototype error. Draft recovery files remain in LocalAppData.\n"+e.Exception.Message,"PDF prototype");e.Handled=true;};
  app.Run(new EditorWindow(args));
 }
}
