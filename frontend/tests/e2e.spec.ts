import { test, expect } from '@playwright/test';

test('homepage renders and allows project creation flow to begin', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page.getByText('Create a Manuscript Project')).toBeVisible();
  await expect(page.getByText('Draft Manuscript')).toBeVisible();
});
