"""Repeat the harness with Python network connections refused (not an OS sandbox)."""
import runpy, socket, sys
def blocked(*args,**kwargs): raise RuntimeError('Network connection blocked during offline validation')
socket.socket.connect=blocked
socket.socket.connect_ex=blocked
socket.create_connection=blocked
sys.argv=['feasibility.py','run']
runpy.run_path('feasibility.py',run_name='__main__')
