const top_bar_with_drawer_css = {
    
    main_container: {
        display: 'flex'
    },
    app_bar_container: { 
        backgroundColor: "#FFFFFF",
        flexGrow: 1
    },
    app_bar_hamburger_icon: { 
        mr: 2,
        borderRadius: "10px",
        border: "1px solid",
        borderColor: "#E0E3E7"
    },
    menu_container: { 
        backgroundColor: "#FFFFFF",
        width:  250 
    },
    app_bar_page_title_contianer: {
        display: {display: "flex"},
        direction: "row",
        alignItems:"center",
        justifyContent: "center"
    },
    app_bar_page_title_text: {
        display: {color: "black", fontWeight: "bold", fontSize: 30}
    },
    app_bar_right_corner_logo: { 
        ml: 2, 
        mr: -2,
        display: {color: "black"}, 
        backgroundColor: 'transparent'
    },
    logo_inside_menu: { 
        padding: 1,
        direction: "column",
        alignItems:"center",
        justifyContent: "center"
    },
    menu_list: { 
        marginTop: -1, 
        marginBottom: -1 
    }
}

export default top_bar_with_drawer_css