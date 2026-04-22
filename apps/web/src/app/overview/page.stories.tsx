import type { Meta, StoryObj } from '@storybook/react';
import OverviewPage from './page';

const meta: Meta<typeof OverviewPage> = {
  title: 'Pages/Overview',
  component: OverviewPage,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<typeof OverviewPage>;

export const Default: Story = {};
