declare module 'simplebar-react' {
  import * as React from 'react';

  export interface SimpleBarProps extends React.HTMLAttributes<HTMLDivElement> {
    scrollableNodeProps?: object;
    children?: React.ReactNode;
  }
  // If not already declared, add this in a types file or above the component:
  interface Message {
    id: number;
    text: string;
    is_bot: boolean;
  }

  export default class SimpleBar extends React.Component<SimpleBarProps> {}
}
