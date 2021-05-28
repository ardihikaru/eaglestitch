import aiohttp_cors

CORS_OPTIONS = {
	"*": aiohttp_cors.ResourceOptions(
		allow_credentials=True,
		expose_headers="*",
		allow_headers="*"
	),
}
