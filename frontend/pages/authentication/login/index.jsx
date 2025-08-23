import React from "react";
import { Box, Button, Card, Container, Divider, Link, Stack, Typography } from "@mui/material";
import IconifyIcon from "../components/base/IconifyIcon";
import LoginForm from "../components/sections/authentication/LoginForm";

const Login = () => {
  return (
    <Box
      style={{
        width: '100%',
        position: 'relative',
        zIndex: 100,
      }}
    >
      <Stack alignItems="center" justifyContent="center" style={{ height: '100%' }}>
        <Container maxWidth="sm">
          <Card
            style={{
              padding: '2rem',
              width: '100%',
            }}
          >
            <Typography variant="h4">Sign In</Typography>

            <Typography
              variant="body2"
              style={{
                marginTop: '1rem',
                marginBottom: '2rem',
                fontSize: '1rem',
              }}
            >
              Don’t have an account?
              <Link
                href="/signup"
                variant="subtitle2"
                style={{ marginLeft: '0.5rem', textDecoration: 'none', color: '#1976d2' }}
              >
                Create One Now!
              </Link>
            </Typography>

            <Stack direction="row" spacing={2}>
              <Button fullWidth size="large" variant="outlined" style={{ padding: '0.5rem' }}>
                <IconifyIcon icon="eva:google-fill" color="red" />
              </Button>
              <Button fullWidth size="large" variant="outlined" style={{ padding: '0.5rem' }}>
                <IconifyIcon icon="gg:facebook" color="#1877f2" />
              </Button>
              <Button fullWidth size="large" variant="outlined" style={{ padding: '0.5rem' }}>
                <IconifyIcon icon="logos:twitter" />
              </Button>
            </Stack>

            <Divider style={{ margin: '2rem 0' }}>
              <Typography variant="body2" style={{ color: 'gray' }}>
                OR
              </Typography>
            </Divider>

            <LoginForm />
          </Card>
        </Container>
      </Stack>
    </Box>
  );
};

export default Login;
