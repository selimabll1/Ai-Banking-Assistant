// src/components/sections/dashboard/index.tsx
import { Grid, Paper, Box, Typography } from '@mui/material';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import UmbrellaIcon from '@mui/icons-material/Umbrella';
import WorkOutlineIcon from '@mui/icons-material/WorkOutline';
import PublicIcon from '@mui/icons-material/Public';
import CurrencyExchangeIcon from '@mui/icons-material/CurrencyExchange';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import ChatDashboard from 'components/ChatDashboard';

const cardSx = {
  p: 3,
  height: { xs: 180, sm: 200, md: 220 },        // ⬆️ bigger cards
  borderRadius: 3,
  position: 'relative',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  gap: 1.25,
  boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
  transition: 'transform .28s ease, box-shadow .28s ease',
  background: 'linear-gradient(180deg,#ffffff 0%, #f7f7f7 100%)',
  '&:hover': {
    transform: 'translateY(-6px)',
    boxShadow: '0 16px 34px rgba(0,0,0,0.12)',
  },
  // accent ribbon
  '&::after': {
    content: '""',
    position: 'absolute',
    top: -32,
    right: -32,
    width: 140,
    height: 140,
    borderRadius: '999px',
    background: 'radial-gradient(closest-side, rgba(155,15,15,.22), transparent 70%)'
  }
};

const iconWrapSx = {
  width: 54,
  height: 54,
  borderRadius: '14px',
  display: 'grid',
  placeItems: 'center',
  color: '#9B0F0F',
  background: 'linear-gradient(140deg, rgba(155,15,15,.10), rgba(155,15,15,.04))',
  border: '1px solid rgba(155,15,15,.18)',
};

const titleSx = {
  fontWeight: 700,
  letterSpacing: .2,
  color: '#223',
};

const descSx = {
  color: '#4a4f58',
  lineHeight: 1.45,
  fontSize: { xs: 14, sm: 15 },
};

const headerWrapSx = {
  mb: 2.5,
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

const headerTitleSx = {
  fontWeight: 800,
  color: '#111',
  fontSize: { xs: 22, sm: 26, md: 28 },
};

const headerSubSx = {
  color: '#6b7079',
  fontSize: { xs: 13, sm: 14 },
};

const services = [
  {
    title: 'FATCA Compliance',
    desc:
      "Toujours soucieuse de mieux servir ses clients, l'ATB permet d’être conforme à la réglementation américaine FATCA.",
    icon: <ShieldOutlinedIcon fontSize="medium" />,
  },
  {
    title: 'Assurance et assistance',
    desc:
      "Protégez-vous, votre famille et vos biens. Des garanties qui s’adaptent à votre mode de vie.",
    icon: <UmbrellaIcon fontSize="medium" />,
  },
  {
    title: 'Gestion de portefeuille',
    desc:
      "ATB assure une forte compétence en matière de gestion de portefeuille.",
    icon: <WorkOutlineIcon fontSize="medium" />,
  },
  {
    title: "Transfert d’argent",
    desc:
      "Envoyez de l’argent rapidement et en toute confiance, au coût le plus bas du marché.",
    icon: <PublicIcon fontSize="medium" />,
  },
  {
    title: 'Opérations de change',
    desc:
      "Client ou non, utilisez nos desks de change présents dans toutes nos agences.",
    icon: <CurrencyExchangeIcon fontSize="medium" />,
  },
  {
    title: 'Tenue de dossier AVA',
    desc:
      "Facilitez vos déplacements professionnels avec l’allocation Voyages d’Affaires.",
    icon: <FlightTakeoffIcon fontSize="medium" />,
  },
];

const Dashboard = () => {
  return (
    <>
      <Box sx={{ px: { xs: 1.5, md: 2.5 } }}>
        {/* Header */}
        <Box sx={headerWrapSx}>
          <Box>
            <Typography variant="h4" sx={headerTitleSx}>
              Nos Services
            </Typography>
            <Typography sx={headerSubSx}>
              Des solutions bancaires adaptées à vos besoins — simples, rapides et sécurisées.
            </Typography>
          </Box>
        </Box>

        {/* Service Cards */}
        <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
          {services.map((s, i) => (
            <Grid key={i} item xs={12} sm={6} lg={4}>
              <Paper elevation={0} sx={cardSx}>
                <Box sx={iconWrapSx}>{s.icon}</Box>
                <Typography variant="h6" sx={titleSx}>
                  {s.title}
                </Typography>
                <Typography sx={descSx}>{s.desc}</Typography>

                {/* CTA area (subtle) */}
                <Box sx={{ mt: 'auto', pt: 1 }}>
                  <Box
                    component="span"
                    sx={{
                      fontSize: 13,
                      color: '#9B0F0F',
                      fontWeight: 600,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: .75,
                      '&:after': {
                        content: '"›"',
                        fontSize: 18,
                        lineHeight: 1,
                        transform: 'translateY(-1px)',
                      },
                    }}
                  >
                    En savoir plus
                  </Box>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Keep your floating chatbot */}
      
    </>
  );
};

export default Dashboard;
