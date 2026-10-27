package com.liskovsoft.smartyoutubetv2.common.app.presenters.settings;

import android.content.Context;

import com.liskovsoft.sharedutils.helpers.MessageHelpers;
import com.liskovsoft.smartyoutubetv2.common.app.models.playback.ui.UiOptionItem;
import com.liskovsoft.smartyoutubetv2.common.app.presenters.AppDialogPresenter;
import com.liskovsoft.smartyoutubetv2.common.app.presenters.base.BasePresenter;
import com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventClient;
import com.liskovsoft.smartyoutubetv2.common.prefs.PartyQueueData;
import com.liskovsoft.smartyoutubetv2.common.utils.SimpleEditDialog;

public final class PartyQueueSettingsPresenter extends BasePresenter<Void> {
    private final PartyQueueData mData;

    private PartyQueueSettingsPresenter(Context context) {
        super(context);
        mData = PartyQueueData.instance(context);
    }

    public static PartyQueueSettingsPresenter instance(Context context) {
        return new PartyQueueSettingsPresenter(context);
    }

    public void show() {
        AppDialogPresenter presenter =
                AppDialogPresenter.instance(getContext());

        presenter.appendSingleSwitch(
                UiOptionItem.from(
                        "PartyQueue Events aktivieren",
                        option -> mData.setEnabled(option.isSelected()),
                        mData.isEnabled()
                )
        );

        presenter.appendSingleButton(
                UiOptionItem.from(
                        "PartyQueue URL: " + shown(mData.getUrl()),
                        option -> edit(
                                "PartyQueue URL",
                                mData.getUrl(),
                                value -> mData.setUrl(value)
                        )
                )
        );

        presenter.appendSingleButton(
                UiOptionItem.from(
                        "Device ID: " + shown(mData.getDeviceId()),
                        option -> edit(
                                "Device ID",
                                mData.getDeviceId(),
                                value -> mData.setDeviceId(value)
                        )
                )
        );

        presenter.appendSingleButton(
                UiOptionItem.from(
                        "Event Token: " + (
                                mData.getToken().isEmpty()
                                        ? "nicht gesetzt"
                                        : "********"
                        ),
                        option -> edit(
                                "Event Token",
                                mData.getToken(),
                                value -> mData.setToken(value)
                        )
                )
        );

        presenter.appendSingleButton(
                UiOptionItem.from(
                        "Verbindung testen",
                        option -> PartyQueueEventClient
                                .instance(getContext())
                                .test((ok, message) ->
                                        MessageHelpers.showLongMessage(
                                                getContext(),
                                                (
                                                        ok
                                                                ? "PartyQueue erreichbar: "
                                                                : "PartyQueue Fehler: "
                                                ) + message
                                        )
                                )
                )
        );

        presenter.showDialog("PartyQueue");
    }

    private void edit(
            String title,
            String currentValue,
            SaveAction saveAction
    ) {
        SimpleEditDialog.show(
                getContext(),
                title,
                currentValue,
                value -> {
                    saveAction.save(value);
                    return true;
                }
        );
    }

    private static String shown(String value) {
        return value == null || value.isEmpty()
                ? "nicht gesetzt"
                : value;
    }

    private interface SaveAction {
        void save(String value);
    }
}