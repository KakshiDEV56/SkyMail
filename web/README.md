# SkyMail Frontend

Next.js frontend for the SkyMail newsletter platform. Handles user authentication, campaign management, template creation, and subscriber lists.

## Setup

### Requirements
- Node.js 18+
- npm or yarn

### Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   ```
   Update `.env.local` with your API URL and Razorpay key.

3. **Start development server:**
   ```bash
   npm run dev
   ```

   Open `http://localhost:3000` in your browser.

## Project Structure

```
app/                    # Next.js app router
├── auth/              # Authentication pages
├── dashboard/         # Main dashboard
│   ├── campaigns/     # Campaign management
│   ├── subscribers/   # Subscriber lists
│   └── templates/     # Email templates
├── landing/           # Landing page
└── page.tsx           # Home page

components/           # Reusable React components
├── dashboard/        # Dashboard components
├── templates/        # Template editor
├── profile/          # User profile
└── ui/              # UI components

lib/                 # Utilities
├── api/             # API client functions
├── hooks/           # Custom React hooks
└── utils/           # Helper functions
```

## Available Scripts

```bash
npm run dev      # Start dev server with hot reload
npm run build    # Build for production
npm start        # Run production build
npm run lint     # Run ESLint
```

## Key Features

- **Authentication:** Company registration, login with JWT
- **Dashboard:** Overview of campaigns and subscribers
- **Campaigns:** Create, schedule, reschedule, and cancel campaigns
- **Templates:** Create email templates with variable placeholders
- **Subscribers:** Import and manage subscriber lists
- **Profile:** Update company information and profile picture
- **Responsive:** Works on desktop, tablet, and mobile

## Template Variables

When creating templates, use these variables:

**System variables (auto-filled):**
- `{{company_name}}` - Your company name
- `{{website_url}}` - Your website
- `{{subscriber_email}}` - Subscriber's email
- `{{subscriber_username}}` - Subscriber's name
- `{{template_asset}}` - Asset URLs (comma-separated)

**Custom variables:**
- Define in campaign constants
- Example: `{{discount}}`, `{{offer_code}}`

## API Integration

The frontend communicates with the backend API at `NEXT_PUBLIC_API_URL`. Common endpoints:

- `POST /api/auth/register` - Company signup
- `POST /api/auth/login` - Login
- `GET/POST /api/campaigns/` - Manage campaigns
- `GET/POST /api/newsletters/templates/` - Email templates
- `GET/POST /api/subscribers/` - Subscriber lists

See backend API docs at `/api/docs` for full details.

## Environment Variables

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_public_key
NEXT_PUBLIC_RAZORPAY_CURRENCY=INR
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Common Issues

**Campaigns not showing up:**
- Ensure backend is running at NEXT_PUBLIC_API_URL
- Check browser console for API errors
- Verify authentication token is stored

**Template preview not updating:**
- Refresh the page
- Check that variables match your custom constants

**File uploads failing:**
- Verify AWS S3 bucket is configured
- Check S3 permissions
- Ensure file size is under 5MB

## Development

The app uses:
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React Query** for API caching
- **Lucide React** for icons

To add a new page:
```bash
# Create app/dashboard/new-feature/page.tsx
```

Changes auto-reload without manual refresh.
