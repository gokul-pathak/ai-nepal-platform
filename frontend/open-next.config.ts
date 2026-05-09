
import { defineOpenNextConfig } from 'open-next/dist/config';

export default defineOpenNextConfig({
  default: {
    override: {
      'aws-lite.config.js': {
        aws: {
          region: 'auto',
          accessKeyId: process.env.CLOUDFLARE_ACCOUNT_ID,
          secretAccessKey: process.env.CLOUDFLARE_API_TOKEN,
        },
      },
    },
  },
  routes: {
    '/tools/{slug}': {
      // Revalidate the page every 60 seconds
      revalidate: 60,
    },
  },
});
