import { test, expect } from '@playwright/test';

test.describe('Authentication Routing', () => {
  test('unauthenticated users are redirected to login', async ({ page }) => {
    // Attempt to access a protected route
    await page.goto('/dashboard');
    
    // Playwright test should see the redirect
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator('text=Welcome back')).toBeVisible();
  });

  test('can navigate to register page', async ({ page }) => {
    await page.goto('/login');
    await page.click('text=Sign up');
    await expect(page).toHaveURL(/.*\/register/);
    await expect(page.locator('text=Create an account')).toBeVisible();
  });
  
  test('can navigate to forgot password page', async ({ page }) => {
    await page.goto('/login');
    await page.click('text=Forgot password?');
    await expect(page).toHaveURL(/.*\/forgot-password/);
    await expect(page.locator('text=Reset Password')).toBeVisible();
  });
});
