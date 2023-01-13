// external deps
import { Link } from "react-router-dom";

// internal deps
import { CellTower, Logo, ModelTraining, StackedLineChart, Tune } from '../icons/Icons';

// state-selectors
import { useAppSelector } from '../../app/hooks';
import { selectTab } from '../../features/status/statusSlice';

// actions
import { useAppDispatch } from '../../app/hooks';
import { changeTab } from '../../features/status/statusSlice';

// styles
import './Tabs.scss';

interface Tab {
  icon  : JSX.Element;
  route : string;
  name  : string;
}

function Tabs() {
  let currentTab = useAppSelector (selectTab);
  const dispatch = useAppDispatch ();

  let tabs: Tab[] = [
    // { icon: Logo,             route: "",              name: ""           },
    { icon: ModelTraining,    route: "flowboard",     name: "Dashboard"  },
    { icon: StackedLineChart, route: "analysisboard", name: "Graphs"     },
    { icon: CellTower,        route: "throughput",    name: "Throughput" },
    { icon: Tune,             route: "settings",      name: "Settings"   }
  ];

  return (
    <div className='homeTabs'>
      <div className="logo">{Logo}</div>
      {tabs.map ((val: Tab, idx: number) => renderTab (val, idx, currentTab, dispatch))}
      {/* <button className="homeTab" type="button">click to expand</button> */}
    </div>
  )
}

let renderTab = (val: Tab, idx: number, iActiveTab: number, dispatch: any) => {
  let isActive = iActiveTab === idx;
  let className  = 'homeTab';
  if (isActive) className += ' active';

  return (
    <Link to={`/${val.route}`} key={`homeTab#${idx}`}>
      <div className={className} onClick={() => dispatch (changeTab (idx))}>
        <div className='tabIcon'> {val.icon}</div>
        <div className='tabLabel'>{val.name}</div>
      </div>
    </Link>
  );
}

export default Tabs;