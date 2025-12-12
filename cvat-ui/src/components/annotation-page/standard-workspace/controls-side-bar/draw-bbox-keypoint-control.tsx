// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import Popover from 'antd/lib/popover';
import Icon from '@ant-design/icons';

import { Canvas } from 'cvat-canvas-wrapper';
import { Canvas3d } from 'cvat-canvas3d-wrapper';
import { ShapeType } from 'cvat-core-wrapper';

import { RectangleIcon } from 'icons';

import DrawShapePopoverContainer from 'containers/annotation-page/standard-workspace/controls-side-bar/draw-shape-popover';
import withVisibilityHandling from './handle-popover-visibility';

export interface Props {
    canvasInstance: Canvas | Canvas3d;
    isDrawing: boolean;
    disabled?: boolean;
}

const CustomPopover = withVisibilityHandling(Popover, 'draw-bbox-keypoint');
function DrawBboxKeypointControl(props: Props): JSX.Element {
    const { canvasInstance, isDrawing, disabled } = props;
    const dynamicPopoverProps = isDrawing ? {
        overlayStyle: {
            display: 'none',
        },
    } : {};

    const dynamicIconProps = isDrawing ? {
        className: 'cvat-draw-bbox-keypoint-control cvat-active-canvas-control',
        onClick: (): void => {
            canvasInstance.draw({ enabled: false });
        },
    } : {
        className: 'cvat-draw-bbox-keypoint-control',
    };

    return disabled ? (
        <Icon className='cvat-draw-bbox-keypoint-control cvat-disabled-canvas-control' component={RectangleIcon} />
    ) : (
        <CustomPopover
            {...dynamicPopoverProps}
            overlayClassName='cvat-draw-shape-popover'
            placement='right'
            content={<DrawShapePopoverContainer shapeType={ShapeType.BBOX_KEYPOINT} />}
        >
            <Icon {...dynamicIconProps} component={RectangleIcon} />
        </CustomPopover>
    );
}

export default React.memo(DrawBboxKeypointControl);
