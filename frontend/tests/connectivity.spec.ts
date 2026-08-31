import { test, expect } from '@playwright/test';

test('backend connectivity', async ({ request }) => {
  // Direct API request to verify backend is up
  const response = await request.get('http://127.0.0.1:8000/api/v1/health');
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data).toHaveProperty('status');
});

test('frontend page loads', async ({ page }) => {
  await page.goto('/');
  // Basic check to see if the React app mounted without crashing
  const root = page.locator('#root');
  await expect(root).toBeVisible();
});
