import type { Meta, StoryObj } from '@storybook/react';
import ScenariosPage from './page';

const meta: Meta<typeof ScenariosPage> = {
  title: 'Pages/Scenarios',
  component: ScenariosPage,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;
type Story = StoryObj<typeof ScenariosPage>;

export const Default: Story = {};
