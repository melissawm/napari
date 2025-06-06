import numpy as np

from napari._vispy.overlays.base import LayerOverlayMixin, VispySceneOverlay
from napari._vispy.visuals.bounding_box import BoundingBox


class VispyBoundingBoxOverlay(LayerOverlayMixin, VispySceneOverlay):
    def __init__(self, *, layer, overlay, parent=None):
        super().__init__(
            node=BoundingBox(),
            layer=layer,
            overlay=overlay,
            parent=parent,
        )
        self.layer.events.set_data.connect(self._on_bounds_change)
        self.overlay.events.lines.connect(self._on_lines_change)
        self.overlay.events.line_thickness.connect(
            self._on_line_thickness_change
        )
        self.overlay.events.line_color.connect(self._on_line_color_change)
        self.overlay.events.points.connect(self._on_points_change)
        self.overlay.events.point_size.connect(self._on_point_size_change)
        self.overlay.events.point_color.connect(self._on_point_color_change)

        self.reset()

    def _on_bounds_change(self):
        bounds = self.layer._display_bounding_box_augmented_data_level(
            self.layer._slice_input.displayed
        )
        if (
            len(self.layer._slice_input.displayed) == 3
            and self.layer.multiscale
        ):
            # for 3D multiscale layers, the lowest data level is displayed
            # and we need the augmented bounding box
            bounds = self.layer._display_bounding_box_at_level(
                self.layer._slice_input.displayed, len(self.layer.data) - 1
            ) + np.array([[-0.5, 0.5]])

        if len(bounds) == 2:
            # 2d layers are assumed to be at 0 in the 3rd dimension
            bounds = np.pad(bounds, ((1, 0), (0, 0)))

        self.node.set_bounds(bounds[::-1])  # invert for vispy

    def _on_lines_change(self):
        self.node.lines.visible = self.overlay.lines

    def _on_points_change(self):
        self.node.markers.visible = self.overlay.points

    def _on_line_thickness_change(self):
        self.node._line_thickness = self.overlay.line_thickness
        self._on_bounds_change()

    def _on_line_color_change(self):
        self.node._line_color = self.overlay.line_color
        self._on_bounds_change()

    def _on_point_size_change(self):
        self.node._marker_size = self.overlay.point_size
        self._on_bounds_change()

    def _on_point_color_change(self):
        self.node._marker_color = self.overlay.point_color
        self._on_bounds_change()

    def reset(self):
        super().reset()
        self._on_line_thickness_change()
        self._on_line_color_change()
        self._on_point_color_change()
        self._on_point_size_change()
        self._on_points_change()
        self._on_bounds_change()
