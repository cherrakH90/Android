/*
 * Copyright (c) 2024 DuckDuckGo
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.duckduckgo.subscriptions.internal.settings

import android.content.Context
import android.util.AttributeSet
import android.view.View
import android.widget.FrameLayout
import android.widget.Toast
import androidx.lifecycle.LifecycleCoroutineScope
import androidx.lifecycle.findViewTreeLifecycleOwner
import androidx.lifecycle.lifecycleScope
import com.duckduckgo.anvil.annotations.InjectWith
import com.duckduckgo.app.di.AppCoroutineScope
import com.duckduckgo.common.ui.viewbinding.viewBinding
import com.duckduckgo.common.utils.DispatcherProvider
import com.duckduckgo.di.scopes.ActivityScope
import com.duckduckgo.di.scopes.ViewScope
import com.duckduckgo.subscriptions.impl.repository.AuthRepository
import com.duckduckgo.subscriptions.internal.SubsSettingPlugin
import com.duckduckgo.subscriptions.internal.databinding.SubsOverrideStartedAtViewBinding
import com.squareup.anvil.annotations.ContributesMultibinding
import dagger.android.support.AndroidSupportInjection
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import javax.inject.Inject

@InjectWith(ViewScope::class)
class OverrideSubscriptionStartedAtView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyle: Int = 0,
) : FrameLayout(context, attrs, defStyle) {

    @Inject
    lateinit var authRepository: AuthRepository

    @Inject
    @AppCoroutineScope
    lateinit var appCoroutineScope: CoroutineScope

    @Inject
    lateinit var dispatcherProvider: DispatcherProvider

    private val binding: SubsOverrideStartedAtViewBinding by viewBinding()

    private val viewCoroutineScope: LifecycleCoroutineScope?
        get() = findViewTreeLifecycleOwner()?.lifecycleScope

    override fun onAttachedToWindow() {
        AndroidSupportInjection.inject(this)
        super.onAttachedToWindow()

        binding.also { base ->
            viewCoroutineScope?.launch(dispatcherProvider.io()) {
                base.subscriptionEnroll.text = (authRepository.getSubscription()?.startedAt ?: 0).toString()
            }

            base.subscriptionEnrollSave.setOnClickListener {
                viewCoroutineScope?.launch(dispatcherProvider.io()) {
                    authRepository.setSubscription(authRepository.getSubscription()?.copy(startedAt = 0L))
                }
                Toast.makeText(context?.applicationContext, "Started At updated", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

@ContributesMultibinding(ActivityScope::class)
class OverrideSubscriptionStartedAtViewViewPlugin @Inject constructor() : SubsSettingPlugin {
    override fun getView(context: Context): View {
        return OverrideSubscriptionStartedAtView(context)
    }
}
