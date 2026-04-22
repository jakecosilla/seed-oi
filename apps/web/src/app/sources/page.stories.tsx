import type { Meta, StoryObj } from '@storybook/react';
import SourcesPage from './page';

const meta: Meta<typeof SourcesPage> = {
  title: 'Pages/Sources',
  component: SourcesPage,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<typeof SourcesPage>;

export const Default: Story = {};
