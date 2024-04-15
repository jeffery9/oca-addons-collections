/* global Webcam */
/*
    Copyright 2016 Siddharth Bhalgami <siddharth.bhalgami@gmail.com>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
*/
odoo.define("web_widget_image_webcam.webcam_widget", function (require) {
    "use strict";

    var core = require("web.core");
    var rpc = require("web.rpc");
    var Dialog = require("web.Dialog");
    const {patch} = require("@web/core/utils/patch");
    const {ImageField} = require("@web/views/fields/image/image_field");

    var _t = core._t;
    var QWeb = core.qweb;

    const getWebcamFlashFallbackModeConfig = rpc.query({
        model: "ir.config_parameter",
        method: "get_webcam_flash_fallback_mode_config",
    });

    patch(ImageField.prototype, "web_widget_image_webcam", {
        async _setWebcamParams() {
            // ::webcamjs:: < https://github.com/jhuckaby/webcamjs >
            // Webcam: Set Custom Parameters
            Webcam.set({
                width: 320,
                height: 240,
                dest_width: 320,
                dest_height: 240,
                image_format: "jpeg",
                jpeg_quality: 90,
                force_flash: (await getWebcamFlashFallbackModeConfig) === "1",
                fps: 45,
                swfURL: "/web_widget_image_webcam/static/src/lib/webcam.swf",
            });
        },

        onWebcamClicked() {
            var self = this,
                WebCamDialog = $(QWeb.render("WebCamDialog")),
                img_data = false;

            self._setWebcamParams();

            var dialog = new Dialog(self, {
                size: "large",
                dialogClass: "o_act_window",
                title: _t("WebCam Booth"),
                $content: WebCamDialog,
                buttons: [
                    {
                        text: _t("Take Snapshot"),
                        classes: "btn-primary take_snap_btn",
                        click: function () {
                            Webcam.snap(function (data) {
                                img_data = data;
                                // Display Snap besides Live WebCam Preview
                                WebCamDialog.find("#webcam_result").html(
                                    '<img src="' + img_data + '"/>'
                                );
                            });
                            if (Webcam.live) {
                                // Remove "disabled" attr from "Save & Close" button
                                $(".save_close_btn").removeAttr("disabled");
                            }
                        },
                    },
                    {
                        text: _t("Save & Close"),
                        classes: "btn-primary save_close_btn",
                        close: true,
                        click: function () {
                            var img_data_base64 = img_data.split(",")[1];

                            /*
                            Size in base64 is approx 33% overhead the original data size.

                            Source: -> http://stackoverflow.com/questions/11402329/base64-encoded-image-size
                                    -> http://stackoverflow.com/questions/6793575/estimating-the-size-of-binary-data-encoded-as-a-b64-string-in-python

                                    -> https://en.wikipedia.org/wiki/Base64
                                    [ The ratio of output bytes to input bytes is 4:3 (33% overhead).
                                    Specifically, given an input of n bytes, the output will be "4[n/3]" bytes long in base64,
                                    including padding characters. ]
                            */

                            // From the above info, we doing the opposite stuff to find the approx size of Image in bytes.
                            var approx_img_size =
                                3 * (img_data_base64.length / 4) -
                                (img_data_base64.match(/[=]+$/g) || []).length;
                            // Like... "3[n/4]"

                            // Upload image in Binary Field
                            self.onFileUploaded({
                                size: approx_img_size,
                                name: "web-cam-preview.jpeg",
                                type: "image/jpeg",
                                data: img_data_base64,
                            });
                        },
                    },
                    {
                        text: _t("Close"),
                        close: true,
                    },
                ],
            }).open();

            dialog.opened().then(function () {
                Webcam.attach("#live_webcam");

                // At time of Init "Save & Close" button is disabled
                $(".save_close_btn").attr("disabled", "disabled");

                // Placeholder Image in the div "webcam_result"
                WebCamDialog.find("#webcam_result").html(
                    '<img src="/web_widget_image_webcam/static/src/img/webcam_placeholder.png"/>'
                );
            });
        },
    });

    Dialog.include({
        destroy: function () {
            // Shut Down the Live Camera Preview | Reset the System
            Webcam.reset();
            this._super.apply(this, arguments);
        },
    });
});
