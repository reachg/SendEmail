#!/usr/bin/env python
import csv
import copy
import csv
import pprint
import re
import smtplib
import time
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template


ASSET_PORTAL_LINKS_TEMPLATE = '''
<li> <a href="https://devportal.intuit.com/app/dp/resource/$asset_id/overview">Service $asset_id Home</a>
    <ul>
     <li> <a href="https://devportal.intuit.com/app/dp/resource/$asset_id/addons/issues">Update JIRA</a></li>
     <li> <a href="https://devportal.intuit.com/app/dp/resource/$asset_id/addons/snow">Update SNOW</a></li>
     </ul>
</li>
'''

def send_email(from_email, to_emails, cc_emails, subject, html_text, plain_text=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ','.join(to_emails)
    msg['Cc'] = ','.join(cc_emails)
    print msg['To']
    print msg['Cc']

    # Create the body of the message (a plain-text and an HTML version).
    text = plain_text or html_text
    html = html_text

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('mailout.data.ie.intuit.net')

    email_targets = copy.deepcopy(to_emails)
    email_targets += cc_emails
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(from_email, email_targets, msg.as_string())
    # message_str = msg.as_string()
    #s.sendmail('gaurav_khanna@intuit.com', 'gaurav_khanna@intuit.com', "test")
    s.quit()

def generate_asset_email_helper(owner, asset_ids, cc):
    links_list = [Template(ASSET_PORTAL_LINKS_TEMPLATE).substitute({'asset_id': asset_id}) for asset_id in asset_ids]
    links = '\n'.join(links_list)

    context = {
        'asset_id': asset_ids[0],
        'owner_name': owner,
        'list_of_service_links': links,
    }

    body = Template(ASSET_JIRA_EMAIL_TEMPLATE).substitute(context)
    html_body = Template(ASSET_JIRA_EMAIL_TEMPLATE_HTML).substitute(context)

    if len(asset_ids) == 1:
        subject = '<ACTION REQUIRED 3rd REMINDER> UPDATE YOUR SERVICE %s IN DEVPORTAL' % (asset_ids[0])
    else:
        subject = '<ACTION REQUIRED 3rd REMINDER> UPDATE YOUR %s SERVICES IN DEVPORTAL' % (len(asset_ids))

    from_email = "Gaurav Khanna <Gaurav_Khanna@intuit.com>"
    to_emails = [owner]
    cc_emails = cc + [from_email]
    send_email(from_email, to_emails, cc_emails, subject, html_body, body)



ASSET_JIRA_EMAIL_TEMPLATE = '''Hello $owner_name,

You are receiving this email because you have one or more services in DevPortal that you created, which do have a JIRA and/or SNOW CI Name populated for the service. Here are the services that we have identified:

$list_of_service_links

OPTION 1: IF YOU DO NOT NEED THIS SERVICE ANYMORE. USE THE FOLLOWING STEPS TO MOVE IT TO TRASH(not needed) OR RETIRE( end of life) IT

STEPS TO MOVE TO TRASH
    1. Make sure you are Admin for the service
    2. Click on the Trash icon to move the service to trash


STEPS TO MOVE TO RETIRED
    1. Make sure you are Admin for the service
    2. Click on "OVERVIEW" in the left nav
    3. Go down to "Life Cycle" and choose "Retired"

OPTION 2: IF THIS IS STILL AN ACTIVE SERVICE. USE THE FOLLOWING STEPS TO ENTER JIRA AND SNOW

STEPS TO UPDATE JIRA
    1. Make sure you are an Admin for the service
    2. Click on the JIRA link above
    3. Enter the JIRA project Name

STEPS TO UPDATE SNOW CI
    1. Make sure you are an Admin for the service
    2. Click on the SNOW link above
    3. Enter the SNOW CI Name

WHEN DO I NEED TO DO THIS BY
ASAP

CANNOT UPDATE?
IF YOU ARE UNABLE TO UPDATE BUT HAVE THE DATA, THEN FEEL FREE TO EMAIL BACK WITH THE DATA AND WE CAN UPDATE THE INFORMATION FOR YOU

WHAT HAPPENS IF I DON'T UPDATE
You will continue to receive this email


Regards,
Gaurav Khanna

'''

ASSET_JIRA_EMAIL_TEMPLATE_HTML = '''\
<html>
  <head></head>
  <body>
    Hello $owner_name,

    <p><b>This is your 3rd reminder.</b></p>

<p>
You are receiving this email because you have <b>one or more services in DevPortal that you created</b>, which do <b>NOT</b> have a JIRA and/or SNOW CI Name populated for the service. Here are the services that we have identified:
</p>
$list_of_service_links

<h3>OPTION 1: IF YOU DO NOT NEED THIS SERVICE ANYMORE. USE THE FOLLOWING STEPS TO MOVE IT TO TRASH(not needed) OR RETIRE( end of life) IT</h3>

<p>
<ol><lh><h4>STEPS TO MOVE TO TRASH</h4></lh>
<li>Make sure you are Admin for the service</li>
<li>Click on the Trash icon to move the service to trash</li>
</ol>
</p>

<ol><lh><h4>STEPS TO MOVE TO RETIRED</h4></lh>
<li>Make sure you are Admin for the service</li>
<li>Click on "OVERVIEW" in the left nav</li>
<li>Go down to "Life Cycle" and choose "Retired"</li>
</ol>

<h3>
OPTION 2: IF THIS IS STILL AN ACTIVE SERVICE. USE THE FOLLOWING STEPS TO ENTER JIRA AND SNOW
</h3>

<ol><lh><h4>STEPS TO UPDATE JIRA</h4></lh>
<li>Make sure you are an Admin for the service</li>
<li>Click on the JIRA link above</li>
<li>Enter the JIRA project Name</li>
</ol>

<ol><lh><h4>STEPS TO UPDATE SNOW CI</h4></lh>
<li>Make sure you are an Admin for the service</li>
<li>Click on the SNOW link above</li>
<li>Enter the SNOW CI Name</li>
</ol>

<h3>
<b>FREQUENTLY ASKED QUESTIONS (FAQs):</b></h3>

<h4><b>1. WHEN DO I NEED TO DO THIS BY?</b></h4>
ASAP

<h4><b>2. WHAT IF I DONT OWN THE SERVICE ANYMORE?</b></h4>
Unfortunately you will continue to receive the email as you created these services in DevPortal. The emails are automated and we cannot change that. Sorry, but you will have to work with the new owners. Once we have the JIRA added to the asset in DevPortal then we can go after the new team for future needs.

<h4><b>3. I AM UNBALE TO UPDATE THE INFORMATION AS I AM NOT AN ADMIN?</b></h4>
If you are unable to update but have the data, then feel free to email back the data and we can update the information for you

<h4><b>4. WHAT HAPPENS IF I DON'T UPDATE?</b></h4>
You will continue to receive this email



<p>
Regards,</p>
<p>Gaurav Khanna</p>
</body>
</html>
'''
def mass_asset_ownership_emails(csv_file, include_vp):

    #generate_asset_email_helper('bhargavan_muthuselvan@intuit.com', '1234', 'bhargavan_muthuselvan@intuit.com')
    print(csv_file)
    with open(csv_file) as csvfile:
        asset_map = {}
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['email'])
            key = (row['email'], row['vp'], row['manager'])
            asset_list = asset_map.get(key) or []
            asset_list.append(row['asset_id'])
            asset_map[key] = asset_list

        for (email, vp, manager), asset_list in asset_map.items():
            ccs = [manager]
            if include_vp:
                ccs.append(vp)
            filtered_ccs = [cc for cc in ccs if cc != "NULL"]
            generate_asset_email_helper(email, asset_list, filtered_ccs)

with open('gaurav_email.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
mass_asset_ownership_emails('gaurav_email.csv', 1)
