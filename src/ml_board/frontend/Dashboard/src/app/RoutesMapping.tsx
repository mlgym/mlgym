import Graphs from '../components/graphs/Graphs';
import Dashboard from '../components/dashboard/Dashboard';
import Settings from '../components/settings/Settings';
import PageNotFound from '../components/error/PageNotFound';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import SettingsIcon from '@mui/icons-material/Settings';

interface RoutesMappingInterface {
    // Object's Key name will be the name shown in Menu List
    [AnyComponent: string]: {
        url: string, // actual url of the page
        component: JSX.Element, // url mapping with the React JSX Component
        showInMenu: Boolean, // true: if that component is needed for navigation from menu
        menuIcon?: JSX.Element | null // icon to show beside component name inside menu
    }
}

export const RoutesMapping:RoutesMappingInterface = {
    Home: {
        url: "",
        component: <Graphs />,
        showInMenu: false,
        menuIcon: null
    },
    Dashboard: {
        url: "dashboard",
        component: <Dashboard />,
        showInMenu: true,
        menuIcon: <DashboardIcon/>
    },
    Graphs: {
        url: "analysisboard",
        component: <Graphs />,
        showInMenu: true,
        menuIcon: <AutoGraphIcon/>
    },
    Settings: {
        url: "settings",
        component: <></>,
        showInMenu: true,
        menuIcon: <SettingsIcon/>
    },
    ErrorComponent: {
        url: "*",
        component: <PageNotFound />,
        showInMenu: false,
        menuIcon: null
    }
}