
function PageNotFound() {
    return(
        <div
            style={{
                backgroundImage: `url(${require("./page_not_found.jpg")})`,
                width: '70%',
                height: '100vh',
                backgroundSize: 'cover',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center',
            }}
        >
        </div>
    )
}

export default PageNotFound