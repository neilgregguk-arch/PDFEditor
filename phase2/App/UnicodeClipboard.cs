using System.Runtime.InteropServices;
using System.Text;
namespace PdfPrototype;
internal static class UnicodeClipboard
{
 public static IntPtr Owner;
 [DllImport("user32.dll",SetLastError=true)]static extern bool OpenClipboard(IntPtr owner);
 [DllImport("user32.dll")]static extern bool CloseClipboard();
 [DllImport("user32.dll")]static extern bool EmptyClipboard();
 [DllImport("user32.dll")]static extern IntPtr GetClipboardData(uint format);
 [DllImport("user32.dll")]static extern IntPtr SetClipboardData(uint format,IntPtr memory);
 [DllImport("kernel32.dll")]static extern IntPtr GlobalAlloc(uint flags,nuint bytes);
 [DllImport("kernel32.dll")]static extern IntPtr GlobalLock(IntPtr memory);
 [DllImport("kernel32.dll")]static extern bool GlobalUnlock(IntPtr memory);
 [DllImport("kernel32.dll")]static extern IntPtr GlobalFree(IntPtr memory);
 static void Open(){for(int i=0;i<5;i++){if(OpenClipboard(Owner))return;Thread.Sleep(15);}throw new IOException($"System clipboard unavailable (Win32 {Marshal.GetLastWin32Error()}). Draft retained; retry on an interactive desktop.");}
 public static string? Read()
 {
  Open();try{var memory=GetClipboardData(13);if(memory==IntPtr.Zero)return null;var p=GlobalLock(memory);try{return Marshal.PtrToStringUni(p);}finally{GlobalUnlock(memory);}}finally{CloseClipboard();}
 }
 public static void Write(string text)
 {
  byte[] bytes=Encoding.Unicode.GetBytes(text+"\0");var memory=GlobalAlloc(2,(nuint)bytes.Length);if(memory==IntPtr.Zero)throw new IOException("Clipboard allocation failed.");bool transferred=false;
  try{var p=GlobalLock(memory);try{Marshal.Copy(bytes,0,p,bytes.Length);}finally{GlobalUnlock(memory);}Open();try{if(!EmptyClipboard()||SetClipboardData(13,memory)==IntPtr.Zero)throw new IOException("Cannot write clipboard.");transferred=true;}finally{CloseClipboard();}}
  finally{if(!transferred)GlobalFree(memory);}
 }
}
