# Provenance and Security Review

## Ownership evidence reviewed

- The canonical project is the author's internship/academic project folder.
- The existing GitHub repository has three commits attributed to the author's GitHub account.
- The accompanying report identifies Manjunath S Vernekar and contains no third-party license or tutorial attribution.
- No copyright header, contributor notice, copied-asset attribution, or conflicting source license was found in the reviewed publishable tree.

These observations support publication of the original source under MIT, but a file review cannot independently prove legal ownership. Third-party libraries are dependencies and remain under their own licenses.

## Public-data boundary

- `intents.json` contains fictional support phrases and original demonstration responses.
- The app asks only for a fictional display alias.
- It does not request or persist email addresses, phone numbers, order IDs, payment details, medical details, passwords, PINs, CVVs, or OTPs.
- Demo responses do not claim that a real transaction, appointment, card action, refund, delivery, or live-agent escalation occurs.

## Security controls in this portfolio build

- real secrets are read only from the environment;
- a random local Flask session key is generated when none is supplied;
- request bodies and maximum message length are validated;
- dynamic text is rendered with DOM `textContent`, not HTML interpolation;
- environment files, caches, virtual environments, logs, IDE state, and build output are ignored;
- automated tests enforce core privacy and response boundaries.

## Production gap

This is a local portfolio demonstration. Production use would additionally require a supported WSGI server, HTTPS, CSRF and rate-limit decisions, authentication/authorization, monitoring, security headers, dependency scanning, model evaluation, and an approved data-governance process.
