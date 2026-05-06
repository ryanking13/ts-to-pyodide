// Adapted from @cloudflare/workers-types email binding types

interface EmailSendResult {
    messageId: string;
}

interface EmailMessage {
    readonly from: string;
    readonly to: string;
}

interface ForwardableEmailMessage extends EmailMessage {
    readonly raw: ReadableStream;
    readonly headers: Headers;
    readonly rawSize: number;
    setReject(reason: string): void;
    forward(rcptTo: string, headers?: Headers): Promise<EmailSendResult>;
    reply(message: EmailMessage): Promise<EmailSendResult>;
}

interface SendEmail {
    send(message: EmailMessage): Promise<EmailSendResult>;
}

declare var emailBinding: SendEmail[];
declare var inbound: ForwardableEmailMessage[];
