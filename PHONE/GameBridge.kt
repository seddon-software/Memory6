class GameBridge(private val context: Context) {

    private val dbHelper = DatabaseHelper(context)

    @JavascriptInterface
    fun getResults(name: String, duration: Int): String {

        var playerName = name
        if (playerName.isEmpty()) playerName = "-"

        if (duration > 0) {
            dbHelper.clearLatest(playerName)
            dbHelper.insertResult(duration, playerName)
        }

        val results = dbHelper.getTopTen(playerName)

        return JSONArray(results).toString()
    }

    @JavascriptInterface
    fun getLastPlayer(): String {
        return dbHelper.getLastPlayer() ?: "-"
    }
}