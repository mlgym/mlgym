import Graphs from '../components/graphs/Graphs';
import Dashboard from '../components/dashboard/Dashboard';
import Settings from '../components/settings/Settings';
import PageNotFound from '../components/error/PageNotFound';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import SettingsIcon from '@mui/icons-material/Settings';

interface RoutesMappingInterface {
    [AnyComponent: string]: {
        url: string,
        component: JSX.Element,
        showInMenu: Boolean,
        menuIcon?: JSX.Element | null
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
        component: <Settings />,
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