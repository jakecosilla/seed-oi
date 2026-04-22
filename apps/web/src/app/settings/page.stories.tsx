import type { Meta, StoryObj } from '@storybook/react';
import SettingsPage from './page';

const meta: Meta<typeof SettingsPage> = {
  title: 'Pages/Settings',
  component: SettingsPage,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<typeof SettingsPage>;

export const Default: Story = {};
