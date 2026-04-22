import type { Meta, StoryObj } from '@storybook/react';
import RisksPage from './page';

const meta: Meta<typeof RisksPage> = {
  title: 'Pages/Risks',
  component: RisksPage,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<typeof RisksPage>;

export const Default: Story = {};
