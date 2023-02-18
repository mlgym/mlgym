const app_css = {
    
    main_container: {
        width: "100%",
        height: "100%"
    },
    fab: {
        position: "fixed",
        bottom: (theme:any) => theme.spacing(6),
        right: (theme:any) => theme.spacing(3),
        opacity: 0.5,
        ":hover": { opacity: 1 }
    },
    filter: {
        borderTopLeftRadius: "10px",
        borderTopRightRadius: "10px",
        paddingLeft: "20px",
        paddingRight: "20px",
        paddingBottom: "30px"
    }
}

export default app_css;