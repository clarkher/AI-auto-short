package com.example.a8_code_battle

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.*
import org.json.JSONObject
import java.io.IOException

class LoginActivity : AppCompatActivity() {
    private val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val etUsername = findViewById<EditText>(R.id.etUsername)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val btnLogin = findViewById<Button>(R.id.btnLogin)

        btnLogin.setOnClickListener {
            val username = etUsername.text.toString()
            val password = etPassword.text.toString()
            if (username.isNotEmpty() && password.isNotEmpty()) {
                loginWithApi(username, password)
            } else {
                Toast.makeText(this, "請輸入帳號與密碼", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun loginWithApi(username: String, password: String) {
        val url = "https://social.cmoney.tw/identity/token"
        val formBody = FormBody.Builder()
            .add("grant_type", "password")
            .add("login_method", "email")
            .add("client_id", "cmstockcommunity")
            .add("account", username)
            .add("password", password)
            .build()
        val request = Request.Builder()
            .url(url)
            .post(formBody)
            .addHeader("Content-Type", "application/x-www-form-urlencoded")
            .build()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = client.newCall(request).execute()
                val responseBody = response.body?.string()
                val isSuccess = response.isSuccessful && responseBody != null &&
                    try {
                        val json = JSONObject(responseBody)
                        json.has("access_token") && json.getString("access_token").isNotEmpty()
                    } catch (e: Exception) {
                        false
                    }
                runOnUiThread {
                    if (isSuccess) {
                        Toast.makeText(this@LoginActivity, "登入成功", Toast.LENGTH_SHORT).show()
                        // TODO: 可導向主畫面或進行後續流程
                    } else {
                        Toast.makeText(this@LoginActivity, "帳號或密碼錯誤", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@LoginActivity, "網路錯誤，請稍後再試", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}