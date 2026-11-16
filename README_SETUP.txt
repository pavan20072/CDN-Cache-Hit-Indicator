CDN CACHE HIT INDICATOR — AWS DEPLOYMENT GUIDE
================================================

PROJECT TYPE
Software-only AWS simulation. No physical hardware is required.

AWS REGION
Use US East (N. Virginia) — us-east-1 for both S3 and Lambda.

FILES
- index.html          Dashboard website
- lambda_function.py Lambda backend
- project.json        Project configuration
- README_SETUP.txt    This guide

IMPORTANT
This project simulates CDN HIT/MISS events. It does NOT connect to CloudFront
or monitor a real CDN. Browser counters/history are local to each browser.
S3 stores only the latest event in status.json.

PART A — CREATE THE S3 WEBSITE BUCKET
-------------------------------------
1. Sign in to https://console.aws.amazon.com/
2. Select region US East (N. Virginia), us-east-1.
3. Search for S3 and open Amazon S3.
4. Click Create bucket.
5. Choose General purpose.
6. Enter a globally unique bucket name, for example:
   cdn-cache-indicator-demo-yourname-2026
   Replace the example with a unique name. Bucket names are globally unique.
7. Keep Object Ownership as ACLs disabled.
8. Under Block Public Access settings, clear "Block all public access"
   and acknowledge the warning. This is needed only because this guide uses
   the S3 website endpoint for a public classroom demonstration.
9. Keep bucket versioning disabled (optional for this demo).
10. Click Create bucket.

PART B — ENABLE STATIC WEBSITE HOSTING
--------------------------------------
1. Open the bucket, then choose Properties.
2. Scroll to Static website hosting and click Edit.
3. Choose Enable.
4. Choose Host a static website.
5. Index document: index.html
6. Error document: index.html
7. Save changes.

PART C — ALLOW PUBLIC READ OF THE DASHBOARD FILE ONLY
-----------------------------------------------------
1. Open the Permissions tab.
2. Find Bucket policy and click Edit.
3. Paste the policy below after replacing YOUR-BUCKET-NAME.

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadDashboard",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/index.html"
    }
  ]
}

4. Save changes.
This grants public read access to index.html only. Do not grant public write
permissions. Lambda will get its own narrowly scoped write permission.

PART D — UPLOAD THE DASHBOARD
-----------------------------
1. Open the bucket's Objects tab.
2. Click Upload, then Add files.
3. Select index.html from this project folder.
4. Click Upload.
5. Return to Properties > Static website hosting.
6. Open the Bucket website endpoint. It should display the dashboard.

The S3 website endpoint is HTTP. Do not use it for sensitive information.

PART E — CREATE THE LAMBDA FUNCTION
-----------------------------------
1. In AWS Console, select region us-east-1.
2. Search for Lambda and choose Create function.
3. Select Author from scratch.
4. Function name: CDNCacheIndicatorFunction
5. Runtime: Python 3.12
6. Architecture: x86_64 (default is fine).
7. Under Permissions, create/use a new basic Lambda execution role.
8. Click Create function.
9. In the Code tab, open lambda_function.py in the editor (or replace
   lambda_function.py contents) with the supplied lambda_function.py code.
10. Click Deploy.

PART F — SET LAMBDA ENVIRONMENT VARIABLES
-----------------------------------------
1. Open Configuration > Environment variables > Edit.
2. Add:
   BUCKET_NAME = your exact S3 bucket name
   STATUS_KEY = status.json
3. Save.

PART G — GIVE LAMBDA PERMISSION TO WRITE status.json
----------------------------------------------------
1. Open the Lambda function's Configuration > Permissions.
2. Click the execution role name to open IAM.
3. In IAM, add an inline policy to the role.
4. Use this policy after replacing YOUR-BUCKET-NAME:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "WriteOnlyCacheStatus",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/status.json"
    }
  ]
}

5. Review and save the policy. Do not grant s3:* or public write access.

PART H — CREATE THE LAMBDA FUNCTION URL
---------------------------------------
1. Open the Lambda function.
2. Choose Configuration > Function URL.
3. Click Create function URL.
4. Auth type: NONE (public educational demonstration only).
5. Configure CORS:
   Allowed origin: your exact S3 website endpoint origin, for example:
   http://YOUR-BUCKET-NAME.s3-website-us-east-1.amazonaws.com
   Allowed methods: POST
   Allowed headers: content-type
6. Save.
7. Copy the Function URL. Anyone who knows an unauthenticated Function URL
   can invoke it. Disable/delete it after your demonstration or add protection.

PART I — CONNECT THE DASHBOARD TO LAMBDA
----------------------------------------
1. Open index.html in a text editor.
2. Find this line:
   const API_URL = "PASTE_YOUR_LAMBDA_FUNCTION_URL_HERE";
3. Replace the placeholder with your exact Lambda Function URL, keeping quotes.
   Example format:
   const API_URL = "https://xxxxxxxx.lambda-url.us-east-1.on.aws/";
4. Save index.html.
5. Upload the updated index.html to the S3 bucket and choose overwrite/confirm
   if prompted.
6. Refresh the S3 website in your browser (hard refresh if needed).

PART J — TEST
-------------
1. Open the S3 website endpoint.
2. Click Simulate Cache HIT. Expected:
   - Green CACHE_HIT status
   - HIT counter increases
   - Browser history updates
   - S3 status.json is created/updated
3. Click Simulate Cache MISS. Expected:
   - Red CACHE_MISS status
   - MISS counter increases
   - Browser history updates
   - S3 status.json is created/updated
4. To inspect the latest event, open S3 > bucket > Objects > status.json.
   You may download/open the object from the AWS console. It is not publicly
   readable under the dashboard-only bucket policy.

TROUBLESHOOTING
---------------
- AccessDenied on status.json: check Lambda execution role policy and bucket name.
- CORS error: the allowed origin must exactly match the S3 website origin,
  including http:// and without an extra path or trailing slash.
- Dashboard says Lambda URL not configured: replace API_URL and upload index.html again.
- 403 on website: confirm static website hosting is enabled and bucket policy
  grants s3:GetObject on the index.html object; confirm Block Public Access settings.
- 404 on website: confirm index.html is at the bucket root and named exactly.
- Function URL 5xx: check Lambda Monitor > View CloudWatch logs.
- If browser counters are cleared, they cannot be recovered from S3; counters are
  intentionally browser-local.

SECURITY AND COST NOTES
-----------------------
- Never put AWS access keys or secrets in index.html.
- Never allow public S3 writes.
- The Function URL with Auth NONE is public. Anyone can invoke it and potentially
  create usage/cost. Restrict or disable it after the classroom demonstration.
- Consider deleting the demo resources when finished to avoid ongoing charges.
- S3 static website hosting does not provide HTTPS directly. For production, use
  a suitable HTTPS hosting design such as CloudFront with private S3 origin.
