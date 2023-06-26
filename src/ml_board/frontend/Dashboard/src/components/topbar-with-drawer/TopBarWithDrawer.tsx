import MenuIcon from '@mui/icons-material/Menu';
import { Container } from '@mui/material';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import * as React from 'react';
import { useLocation, useNavigate } from "react-router-dom";
import { RoutesMapping } from '../../app/RoutesMapping';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { changeTab, selectTab } from '../../redux/globalConfig/globalConfigSlice';
import { LogoOnly, LogoText } from "../../svgs_and_imgs/Icons";
import Statistics from '../statistics/Statistics';
// styles
import styles from './TopBarWithDrawer.module.css';

export default function TopBarWithDrawer() {

    const location = useLocation();
    let currentTab = useAppSelector(selectTab);
    const dispatch = useAppDispatch();
    const [state, setState] = React.useState({
        menuDrawer: false,
    });

    React.useEffect(() => {
        if(location.pathname.split("/")[1] !== "" && currentTab !== location.pathname.split("/")[1]) {
            // Select the menu tab as per the url name
            dispatch(changeTab(location.pathname.split("/")[1]));
        }
        else if (location.pathname.split("/")[1] === "") {
            // if the app started directly, then the home page would be Graphs. So the graphs tab should be selected in the menu
            dispatch(changeTab(RoutesMapping.Graphs.url));
        }
    }, [location.pathname])

    const toggleMenuDrawer = (drawerState: string, open: boolean) => {
        setState({ ...state, [drawerState]: open });
    };

    const navigate = useNavigate();

    const changeTabRequest = (text:string) => {
        toggleMenuDrawer("menuDrawer", false)
        dispatch(changeTab(text));
        navigate(text);
    }

    const menu_list = () => (
    <Box
        className={styles.menu_container}
        role="presentation"
        // onClick={()=>toggleMenuDrawer("menuDrawer", false)}
    >
        {/* MLGym Logo with Text */}
        <Container className={styles.logo_inside_menu}>
            {LogoText}
        </Container>
        <Divider/>
        {/* Menu Items */}
        <List className={styles.menu_list}>
            {/* Iterate through the Dynamic Routes and check which component's name to display in the Menu and then Navigate to the destination URL on selection / click of that component */}
            {
                Object.keys(RoutesMapping)
                .filter((routeMapKey)=> RoutesMapping[routeMapKey].showInMenu)
                .map((routeMapKey, index) => (
                    <ListItem key={index} disablePadding onClick={() => changeTabRequest(RoutesMapping[routeMapKey].url)}>
                        <ListItemButton selected={RoutesMapping[routeMapKey].url === currentTab}>
                            <ListItemIcon>
                                {RoutesMapping[routeMapKey].menuIcon}
                            </ListItemIcon>
                            <ListItemText primary={routeMapKey} />
                        </ListItemButton>
                    </ListItem>
                ))
            }
        </List>
        <Divider />
        <Statistics/>
    </Box>
    );

  return (
    <Box className={styles.main_container}>
        {/* Title Bar */}
        <AppBar 
            component="nav"
            className={styles.app_bar_container}
        >
            <Toolbar>
                {/* Hamburger Menu Icon */}
                <IconButton
                    size="large"
                    edge="start"
                    aria-label="open drawer"
                    className={styles.app_bar_hamburger_icon}
                    onClick={()=>toggleMenuDrawer("menuDrawer", true)}
                >
                    <MenuIcon />
                </IconButton>
                
                {/* Page Title Text Goes Here */}
                <Container
                    className={styles.app_bar_page_title_contianer}
                >
                    <Typography
                        component="div"
                        variant="h6"
                        className={styles.app_bar_page_title_text}
                    >
                        {/* 
                            Just capitalizing the first letter of the selected page name. As the name from `location.pathname.split("/")[1]` would be the same as RoutesMapping.<MenuKey>.url --> it will be in lowercase.
                            And, if the URL === "" then it's the home page, which will be the Graphs page by default. 
                        */}
                        {
                            currentTab.charAt(0).toUpperCase() + currentTab.slice(1)
                        }
                    </Typography>
                </Container>

                {/* MLGym Logo at the end of the title bar */}
                <IconButton
                    size="small"
                    edge="end"
                    className={styles.app_bar_right_corner_logo}
                    disabled={true}
                >
                    {LogoOnly}
                </IconButton>
            </Toolbar>
        </AppBar>
        <Toolbar/> {/* This acts as a padding buffer for the area under the TopBarWithDrawer and nothing more! */}
        {/* Drawer Menu */}
        <React.Fragment>
            <Drawer
                variant="temporary"
                anchor={"left"} // MUI-Drawer property: tells from which side of the screen, the drawer should appear
                open={state["menuDrawer"]}
                onClose={()=>toggleMenuDrawer("menuDrawer", false)}
            >
                {menu_list()}
            </Drawer>
        </React.Fragment>
    </Box>
  );
}