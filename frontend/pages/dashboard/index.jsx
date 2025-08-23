import React from 'react';
import { Grid } from '@mui/material';

import WeeklyActivity from '../../../components/sections/dashboard/activity/WeeklyActivity';
import BalanceHistory from '../../../components/sections/dashboard/balance/BalanceHistory';
import MyCards from '../../../components/sections/dashboard/creditCards/MyCards';
import ExpenseStatistics from '../../../components/sections/dashboard/expense/ExpenseStatistics';
import InvoiceOverviewTable from '../../../components/sections/dashboard/invoice/InvoiceOverviewTable';
import RecentTransactions from '../../../components/sections/dashboard/transactions/RecentTransaction';
import QuickTransfer from '../../../components/sections/dashboard/transfer/QuickTransfer';

const Dashboard = () => {
  return (
    <Grid container spacing={3} style={{ marginBottom: '24px' }}>
      {/* Cards */}
      <Grid item xs={12} xl={8} style={{ zIndex: 1 }}>
        <MyCards />
      </Grid>
      <Grid item xs={12} xl={4} style={{ zIndex: 1 }}>
        <RecentTransactions />
      </Grid>

      {/* Charts */}
      <Grid item xs={12} lg={8} style={{ zIndex: 1 }}>
        <WeeklyActivity />
      </Grid>
      <Grid item xs={12} lg={4}>
        <ExpenseStatistics />
      </Grid>

      {/* Sliders */}
      <Grid item xs={12} lg={6} style={{ zIndex: 1 }}>
        <QuickTransfer />
      </Grid>
      <Grid item xs={12} lg={6} style={{ zIndex: 1 }}>
        <BalanceHistory />
      </Grid>

      {/* Data Table */}
      <Grid item xs={12}>
        <InvoiceOverviewTable />
      </Grid>
    </Grid>
  );
};

export default Dashboard;
