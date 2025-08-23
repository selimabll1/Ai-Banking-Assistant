import React from 'react';
import { Box, Card, Stack, Typography } from '@mui/material';
import ResetPasswordForm from '../components/sections/authentication/ResetPasswordForm'; // ✅ Adjust the path as needed

const ResetPasswordPage = () => {
  return (
    <Box
      sx={{
        width: '100%',
        position: 'relative',
        zIndex: 100,
      }}
    >
      <Stack alignItems="center" justifyContent="center" sx={{ height: '100vh' }}>
        <Card
          sx={{
            padding: { xs: 3, sm: 5 },
            width: '100%',
            maxWidth: 480,
          }}
        >
          <Typography variant="h4">Reset Password</Typography>

          <Typography variant="subtitle1" color="text.secondary" sx={{ mt: 2, mb: 5 }}>
            Please enter your new password and confirm it below.
          </Typography>

          <ResetPasswordForm />
        </Card>
      </Stack>
    </Box>
  );
};

export default ResetPasswordPage;
