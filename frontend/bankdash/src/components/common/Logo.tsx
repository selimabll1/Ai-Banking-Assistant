import { Typography } from '@mui/material';
import Image from 'components/base/Image';
import { Fragment } from 'react/jsx-runtime';

export default function Logo() {
  return (
    <div className="d-flex align-items-center gap-2">
      <span style={{fontWeight:700, color:"#9B0F0F"}}>ATB</span>
      <span className="text-muted d-none d-sm-inline">Dashboard</span>
    </div>
  );
}

