import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import Dashboard from '../components/dashboard/Dashboard';
import PageNotFound from '../components/error/PageNotFound';
import ExperimentPage from '../components/experimentPage/ExperimentPage';
import ModelCard from '../components/modelCard/ModelCard';
import Graphs from '../components/graphs/Graphs';

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
    ExperimentPage: {
        url: "experiment",
        component: <ExperimentPage/>,
        showInMenu: false,
        menuIcon: null
    },
    ModelCard: {
        url: "modelcard",
        component: <ModelCard/>,
        showInMenu: false,
        menuIcon: null
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