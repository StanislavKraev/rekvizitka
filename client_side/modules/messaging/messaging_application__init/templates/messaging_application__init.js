{% load js_utils %}
YUI.add('messaging_application__init', function(Y) {
    Y.namespace('MessagingAppSettings_init');
    $.extend(Y.MessagingAppSettings_init, {
        fetchUrl : "/messages/c/",
        hashNavBaseUrl : "messages/",
        messagesOnPage : {{ user_message_settings.messages_on_page }},
        contactsOnPage : {{ user_message_settings.contacts_on_page }},
        onlyFromContactList : {% bool_to_js user_message_settings.only_from_contact_list %},
        isOnAutoAnswer : {% bool_to_js user_message_settings.is_on_auto_answer %},
        textAutoAnswer : '{{ user_message_settings.text_auto_answer }}',
        textSignature : '{{ user_message_settings.text_signature }}',
        defaultMailFolder : '{{ default_mail_folder }}',
        folderList : [
                        ['InboxFolder','{{ message_folders.inbox_folder.0 }}',{{ message_folders.inbox_folder.1 }}],
                        ['OutboxFolder','{{ message_folders.sent_folder.0 }}',{{ message_folders.sent_folder.1 }}],
                        ['SpamFolder','{{ message_folders.spam_folder.0 }}', {{ message_folders.spam_folder.1 }}],
                        ['DraftFolder','{{ message_folders.draft_folder.0 }}', {{ message_folders.draft_folder.1 }}],
                        ['DeletedFolder', '{{ message_folders.deleted_folder.0 }}', {{ message_folders.deleted_folder.1 }}]
        ]
    });
});
