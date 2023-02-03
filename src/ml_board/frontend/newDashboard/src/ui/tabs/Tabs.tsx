// external deps
import { Link } from "react-router-dom";

// internal deps
import { flag } from '../icons/Icons';
// import { dashboard       } from '../icons/Icons';
import { cellTowerIcon, chartsMixedIcon, slidersIcon } from '../icons/Icons';

// state-selectors
import { useAppSelector } from '../../app/hooks';
import { selectTab } from '../../redux/status/statusSlice';

// actions
import { useAppDispatch } from '../../app/hooks';
import { changeTab } from '../../redux/status/statusSlice';

// styles
import './Tabs.scss';

interface Tab {
  icon  : JSX.Element;
  route : string;
  name  : string;
  id    :string; // class name
}

function Tabs() {
  let currentTab = useAppSelector (selectTab);
  const dispatch = useAppDispatch ();

  let tabs: Tab[] = [
    // { icon: logo,            route: "",              name: ""           },
    { icon: flag,            route: "dashboard",     name: "Dashboard"  , id:"Dashboard" },
    { icon: chartsMixedIcon, route: "analysisboard", name: "Graphs"     , id:"Chartboard" },
    { icon: cellTowerIcon,   route: "throughput",    name: "Throughput" , id:"Throughput" },
    { icon: slidersIcon,     route: "settings",      name: "Settings"   , id:"Settings" }

  ];

  return (
    <div className='homeTabs'>
      {tabs.map ((val: Tab, _: number) => renderTab (val, val.id, currentTab, dispatch))}
    </div>
  )
}

let renderTab = (val: Tab, id:string, iActiveTab: string, dispatch: any) => {
  let isActive = iActiveTab === id;
  let className  = 'homeTab';
  if (isActive) className += ' active';

  return (
    <Link to={`/${val.route}`} key={`homeTab#${id}`}>
      <div className={className} onClick={() => dispatch (changeTab (id))}>
        <div className='tabIcon'> {val.icon}</div>
        <div className='tabLabel'>{val.name}</div>
      </div>
    </Link>
  );
}

export default Tabs;