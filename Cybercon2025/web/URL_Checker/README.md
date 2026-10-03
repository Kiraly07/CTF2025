# Writeup – URL Checker

## Vulnerability Summary

The challenge involved exploiting a **Server-Side Request Forgery (SSRF)** vulnerability in a WordPress site, chained with a **time-based blind SQL injection** inside the `w2dc_get_map_marker_info` AJAX action. By abusing the SSRF entry point, we were able to reach internal WordPress endpoints and extract sensitive data, including the flag stored in the `wp_options` table.

## Step 1: Identifying the SSRF

The web application exposed an endpoint:

```
http://<CHALL_HOST>/?u=<internal_url>&b=<body>
```

**Parameters:**

- `u`: destination URL for SSRF (internal request).  
- `b`: body data for POST forwarding.  

By supplying internal targets such as:

```
http://127.0.0.1/cms/wp-admin/admin-ajax.php
http://localhost/cms/wp-admin/admin-ajax.php
http://[::1]/cms/wp-admin/admin-ajax.php
```

we confirmed that the server made internal requests on our behalf.  
The internal endpoint accepted the vulnerable action:

```
action=w2dc_get_map_marker_info
```

---

## Step 2: Blind SQL Injection (Timing-based)

The parameter `locations_ids[]` was injectable. By sending:

```sql
(SELECT BENCHMARK(1000000, MD5(1)))
```

we observed significant response delays compared to baseline requests. This confirmed a **time-based blind SQL injection** vulnerability.

---

## Step 3: Building a Timing Oracle

We used the following logic:

```sql
(SELECT IF(<condition>, BENCHMARK(N, MD5(1)), 0))
```

- If the condition is **true**, the query takes much longer.  
- If **false**, response time stays near baseline.  

This provided a reliable **boolean oracle** to extract data character-by-character.

---

## Step 4: Extracting the Flag

The flag was stored in `wp_options` under `option_name='ctf_flag'`.  
Our injection payload targeted:

```sql
ASCII(SUBSTRING((SELECT option_value 
                 FROM wp_options 
                 WHERE option_name=CHAR(99,116,102,95,102,108,97,103)),
                 {pos},1))
```

Using a **binary search** over ASCII characters, we leaked the flag one character at a time until encountering the closing `}`.

---

## Step 5: Automation

We automated the process with Python:

- **Calibration**: measure baseline and benchmark timings to set a threshold.  
- **Oracle**: run payloads with `IF(...,BENCHMARK,0)` and compare response times.  
- **Binary Search**: extract each character efficiently (O(logN) probes per char).  
- **Termination**: stop after reading `}`.  

The script successfully retrieved the full flag.

---

## Impact

- **SSRF**: attacker can pivot into the internal network.  
- **SQL Injection**: arbitrary data extraction from WordPress database.  
- **Flag Disclosure**: sensitive secrets are compromised.  

This chained vulnerability demonstrates how SSRF + SQLi can lead to **complete compromise of application data**.

---

## Mitigations

1. **Restrict SSRF**: validate and whitelist outbound request targets. Disallow `127.0.0.1`, `localhost`, or private IP ranges.  
2. **Harden WordPress Plugins**: sanitize SQL inputs using prepared statements.  
3. **Monitoring**: detect abnormal response times or suspicious internal requests.  
4. **Authentication**: sensitive admin-ajax actions should require proper authentication.  

---

## Conclusion

The challenge exploited a **time-based blind SQL injection via SSRF** in a WordPress AJAX action. By carefully measuring delays and automating character extraction, we successfully leaked the secret flag from the database.

<img width="1016" height="855" alt="image" src="https://github.com/user-attachments/assets/e06968a3-09d5-412c-a56a-46fc8a558028" />


