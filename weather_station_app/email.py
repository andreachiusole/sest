from django.conf import settings
# pip install postmarker


def send_email_wrapper(from_field, to_list, subject, text_body=None,
                       html_body=None):
    """Just a wrapper around different third-party services used to send email.

    So far, I only pass the arguments from this function to another one, but
    I plan to introduce a smart system that takes into account the number of
    emails sent with each third-party service, in order to use free credits
    from many different services.
    """

    if not html_body and not text_body:
        raise TypeError("A html or a text body has to be provided.")

    # TODO: check whether to_list is actually a single string, and in case
    # convert it to a list of recipients (made of a single object) before
    # passing it to other functions.
    # isinstance(to_list, str) # py3 specific
    return send_email_postmark(from_field, to_list, subject, text_body,
                               html_body)


def send_email_postmark(from_field, to_list, subject, text_body=None,
                        html_body=None):
    """Postmark[app.com] API client.

    In order to use the postmark service, visit their website, register a
    (free) user, create a sending server, get its token (Credentials >
    Server API) and save it into settings.py. Then instantiate a PM Client
    object to be called from this function.
    """

    # Maybe using send_batch in case of multiple recipients could be better?
    for recipient in to_list:

        # I use the postmark client object instantiated in the settings file.
        return settings.POSTMARK_CLIENT.emails.send(
            Subject=subject,
            # Text and Html bodies can be sent together into a multipart email.
            TextBody=text_body,
            HtmlBody=html_body,
            From=from_field,
            To=recipient,
        )
