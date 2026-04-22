import type { Meta, StoryObj } from '@storybook/react';
import { SidePanel } from './SidePanel';

const meta: Meta<typeof SidePanel> = {
  title: 'UI/SidePanel',
  component: SidePanel,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof SidePanel>;

export const Left: Story = {
  args: {
    side: 'left',
    width: '300px',
    children: <div className="p-4 italic text-slate-500 text-sm">Left Side Panel Content</div>,
  },
};

export const Right: Story = {
  args: {
    side: 'right',
    width: '400px',
    children: <div className="p-4 italic text-slate-500 text-sm">Right Side Panel Content</div>,
  },
};
