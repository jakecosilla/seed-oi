# Seed OI Frontend Quality Guide

To ensure UI regressions are caught early and components are properly isolated, we employ **Vitest** for unit testing and **Storybook** for component-driven development.

## Running Tests Locally
We use Vitest to run all unit and component tests.
```bash
cd apps/web
npm run test
```

## Running Storybook
Storybook serves as a playground and visual catalog for all reusable UI components (e.g., Cards, Badges, SidePanels).
```bash
cd apps/web
npm run storybook
```

## Guidelines for Scalability
- **Shared Components:** Every generic component in `src/components/ui/` must have a corresponding `.stories.tsx` and `.test.tsx` file.
- **Complex Features:** Abstract business logic out of UI components to keep them pure. Use Storybook for testing visual states (loading, error, success) and Vitest for testing state management and routing hooks.
