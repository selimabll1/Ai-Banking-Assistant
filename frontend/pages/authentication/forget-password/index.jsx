import React from 'react';
import { Box, Card, Stack, Typography } from '@mui/material';
import ForgetPasswordForm from '../components/sections/authentication/ForgotPasswordForm'; // ✅ Update the path if needed

const ForgetPasswordPage = () => {
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
          <Box padding={1}>
            <Typography variant="h4" fontWeight={700}>
              Forgot your password?
            </Typography>

            <Typography
              color="text.secondary"
              variant="body1"
              fontWeight={400}
              sx={{ mb: 2.5, mt: 1.5 }}
            >
              Please enter the email address associated with your account.
            </Typography>

            <ForgetPasswordForm />
          </Box>
        </Card>
      </Stack>
    </Box>
  );
};

export default ForgetPasswordPage;
