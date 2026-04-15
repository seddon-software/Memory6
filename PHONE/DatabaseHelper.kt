package com.example.memorygame

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.text.SimpleDateFormat
import java.util.*

class DatabaseHelper(context: Context) :
    SQLiteOpenHelper(context, "games.db", null, 1) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE IF NOT EXISTS results (
                time INTEGER,
                date TEXT,
                name TEXT,
                latest TEXT
            )
        """.trimIndent())
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Not needed yet
    }

    // 🔁 Clear latest flag for this player
    fun clearLatest(name: String) {
        val db = writableDatabase
        db.execSQL(
            "UPDATE results SET latest = ' ' WHERE name = ?",
            arrayOf(name)
        )
    }

    // ➕ Insert new result
    fun insertResult(time: Int, name: String) {
        val db = writableDatabase

        val date = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
            .format(Date())

        val values = ContentValues().apply {
            put("time", time)
            put("date", date)
            put("name", name)
            put("latest", "*")
        }

        db.insert("results", null, values)
    }

    // 🏆 Get top 10 results
    fun getTopTen(name: String): List<String> {
        val db = readableDatabase
        val results = mutableListOf<String>()

        val query: String
        val args: Array<String>?

        if (name == "-") {
            query = """
                SELECT time, date, latest 
                FROM results 
                ORDER BY time ASC, date DESC 
                LIMIT 10
            """.trimIndent()
            args = null
        } else {
            query = """
                SELECT time, date, latest 
                FROM results 
                WHERE name = ? 
                ORDER BY time ASC, date DESC 
                LIMIT 10
            """.trimIndent()
            args = arrayOf(name)
        }

        val cursor = db.rawQuery(query, args)

        while (cursor.moveToNext()) {
            val time = cursor.getInt(0)
            var date = cursor.getString(1)
            val latest = cursor.getString(2)

            // Add "*" to latest result (matches your Flask logic)
            if (latest == "*") {
                date += "*"
            }

            results.add("$time $date")
        }

        cursor.close()
        return results
    }

    // 👤 Get last player
    fun getLastPlayer(): String? {
        val db = readableDatabase

        val cursor = db.rawQuery(
            "SELECT name FROM results ORDER BY date DESC LIMIT 1",
            null
        )

        var player: String? = null

        if (cursor.moveToFirst()) {
            player = cursor.getString(0)
        }

        cursor.close()
        return player
    }
}
