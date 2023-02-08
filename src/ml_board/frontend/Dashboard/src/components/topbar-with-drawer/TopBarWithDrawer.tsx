import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import MenuIcon from '@mui/icons-material/Menu';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Drawer from '@mui/material/Drawer';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import SettingsIcon from '@mui/icons-material/Settings';
import SportsBarIcon from '@mui/icons-material/SportsBar';

type Anchor = 'left';

export default function TopBarWithDrawer() {

    const [state, setState] = React.useState({
        left: false,
    });

  const toggleDrawer =
  (anchor: Anchor, open: boolean) =>
  (event: React.KeyboardEvent | React.MouseEvent) => {
    if (
      event.type === 'keydown' &&
      ((event as React.KeyboardEvent).key === 'Tab' ||
        (event as React.KeyboardEvent).key === 'Shift')
    ) {
      return;
    }

    setState({ ...state, [anchor]: open });
    };

    const list = (anchor: Anchor) => (
    <Box
        sx={{ 
            backgroundColor: "#FFFFFF",
            width:  250 
        }}
        role="presentation"
        onClick={toggleDrawer(anchor, false)}
        onKeyDown={toggleDrawer(anchor, false)}
    >
        <List>
        {['Dashboard', 'Graphs', 'Settings'].map((text, index) => (
            <ListItem key={text} disablePadding>
            <ListItemButton>
                <ListItemIcon>
                    {
                        text === "Dashboard" ?
                        <DashboardIcon/>
                        :
                        text === "Graphs" ?
                        <AutoGraphIcon/>
                        :
                        text === "Settings" ?
                        <SettingsIcon/>
                        :
                        <SportsBarIcon/>
                    }
                </ListItemIcon>
                <ListItemText primary={text} />
            </ListItemButton>
            </ListItem>
        ))}
        </List>
        {/* <Divider /> */}
    </Box>
    );

  return (
    <Box sx={{ display: 'flex' }}>
        <AppBar 
            component="nav" 
            sx={{ 
                backgroundColor: "#FFFFFF",
                flexGrow: 1
            }}
        >
            <Toolbar>
                <IconButton
                    size="large"
                    edge="start"
                    aria-label="open drawer"
                    sx={{ 
                        mr: 2,
                        borderRadius: "10px",
                        border: "1px solid",
                        borderColor: "#E0E3E7"
                    }}
                    onClick={toggleDrawer("left", true)}
                >
                    <MenuIcon />
                </IconButton>
                <div>
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{ 
                            display: { xs: 'none', sm: 'block', color: "black", fontWeight: "bold" }
                        }}
                    >
                        MLGym
                    </Typography>
                </div>
            </Toolbar>
        </AppBar>
        <Box component="nav">
            <Drawer
                variant="temporary"
                anchor={"left"}
                open={state["left"]}
                onClose={toggleDrawer("left", false)}
            >
                {list("left")}
            </Drawer>
        </Box>
    </Box>
  );
}