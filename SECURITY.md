# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Do NOT

- Do not open a public GitHub issue
- Do not disclose the vulnerability publicly before it has been addressed

### Do

1. **Email the maintainers directly** with details about the vulnerability
2. **Include the following information:**
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment:** Within 48 hours of your report
- **Initial Assessment:** Within 1 week
- **Resolution Timeline:** Depending on severity, typically 2-4 weeks
- **Credit:** We will credit you in the security advisory (unless you prefer anonymity)

## Security Best Practices for Deployment

When deploying SyteScan, ensure:

1. **Environment Variables:** Never commit `.env` files or secrets to version control
2. **HTTPS:** Always use HTTPS in production
3. **File Uploads:** Validate file types and sizes; scan for malware in production
4. **Database:** Use strong passwords; consider PostgreSQL for production
5. **CORS:** Restrict origins to your domains only
6. **Dependencies:** Regularly update dependencies to patch known vulnerabilities

## Known Security Considerations

- File uploads are validated but should be scanned in production environments
- SQLite is suitable for development; use PostgreSQL with proper credentials for production
- The application does not currently implement rate limiting (implement via nginx/load balancer)

## Contact

For security concerns, contact the project maintainers directly.
