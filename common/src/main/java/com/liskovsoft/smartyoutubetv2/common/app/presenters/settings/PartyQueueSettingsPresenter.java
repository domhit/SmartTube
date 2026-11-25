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
                                presenter,
                                "PartyQueue Server-URL",
                                mData.getUrl(),
                                value -> mData.setUrl(value)
                        )
                )
        );

        presenter.appendSingleButton(
                UiOptionItem.from(
                        "Device ID: " + shown(mData.getDeviceId()),
                        option -> edit(
                                presenter,
                                "PartyQueue Device-ID",
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
                        option -> editPassword(
                                presenter,
                                "Gemeinsamer PartyQueue Event-Token",
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
            AppDialogPresenter presenter,
            String title,
            String currentValue,
            SaveAction saveAction
    ) {
        // Close the settings sidebar before opening the Android edit dialog.
        // Otherwise the dialog is rendered behind the sidebar and the OK key
        // can be delivered to the still-active settings item a second time.
        presenter.closeDialog();
        SimpleEditDialog.show(
                getContext(),
                title,
                currentValue,
                value -> {
                    saveAction.save(value.trim());
                    return true;
                }
        );
    }

    private void editPassword(
            AppDialogPresenter presenter,
            String title,
            String currentValue,
            SaveAction saveAction
    ) {
        presenter.closeDialog();
        SimpleEditDialog.showPassword(
                getContext(),
                title,
                currentValue,
                value -> {
                    saveAction.save(value.trim());
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