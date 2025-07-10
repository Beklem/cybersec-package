#mainly inspired by my own mum, since she got her first *scary* spoofed email - i'll build this and see how to reverse engineer it :P
#DO NOT RUN THIS CODE!

#got a spamhaus message, but i don't wanna do BAD stuff (this was a literal test)



































import dns.resolver
import sys
import smtplib #smtp is the protocol for email communication 

def findMXServer(domain):
    print(f"[*] Looking up MX Record for {domain}....")

    try:
        mxRecords = dns.resolver.resolve(domain, 'MX')
        sortedRecords = sorted(mxRecords, key = lambda record: record.preference)
        mailServer = sortedRecords[0].exchange.to_text()
        print(f"[*] Found Mail Server: {mailServer}")
        return mailServer
    except Exception as e:
        print(f"[!] Couldn't find mail server for {domain}: {e}")
        return None

def sendEmail(toEmail, fakeEmail, fakeName, subject, content):
    try:
        recipientDomain = toEmail.split("@")[1]
    except IndexError:
        print(f"[!] Invalid recipient email address: {toEmail}")
        return

    #find mail server for that domain
    smtpServer = findMXServer(recipientDomain)
    if not smtpServer:
        print("[!] No mail server found!")
        return

    smtpPort = 25 #this is for unauthenticated smtp

    #email construction
    message = f"From: {fakeName} <{fakeEmail}>\n"
    message += f"To: {toEmail}"
    message += f"Subject: {subject}\n\n"
    message += content

    print(f"\n[*] Attempting to send email via {smtpServer}")

    try:
        server = smtplib.SMTP(smtpServer, smtpPort, timeout = 5)
        server.sendmail(fakeEmail, toEmail, message)
        server.quit()
        print("[*] Email sent successfully! Probably blocked by spam :P")

    except Exception as e:
        print(f"[!] Failed to send email: {e}")

def main():
    spoofedEmailAddress = "beklemkubak@gmail.com"
    spoofedName = "beklem k"

    recipientEmailAddress = "beklemkubak@outlook.com"

    subject = "Urgent! This is a silly test."
    body = "This is a spoofed email, I wanna reverse engineer this to see if we can actually do something about spoofed emails forever :P"

    sendEmail(recipientEmailAddress, spoofedEmailAddress, spoofedName, subject, body)

if __name__ == "__main__":
    main()

